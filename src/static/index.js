const inputChat = document.querySelector("#input-chat");
const resLog = document.querySelector("#res-log");
const historyContainer = document.querySelector(".history");
let sessions = {};
let current_session_id = null;
let uri = "/api/mychat_pure";

fetch('chat_history.json')
  .then(response => {
    if (!response.ok) {
      throw new Error('网络响应不正常');
    }
    return response.json(); // 解析 JSON 数据
  })
  .then(data => {
    console.log('成功读取数据:', data);

    // 遍历所有时间戳
    Object.keys(data).forEach(timestamp => {
      const messages = data[timestamp];
      console.log('时间戳:', timestamp);

      // 创建新的会话对象
      const sessionMessages = messages.map(message => {
        return {
          content: message.content,
          type: message.type === 'human' ? 'self' : 'llm'
        };
      });

      // 将消息存入 sessions 对象，并设置 name 属性
      sessions[timestamp] = {
        name: sessionMessages[0].content.length > 8 ? sessionMessages[0].content.substring(0, 8) : sessionMessages[0].content,
        messages: sessionMessages
      };

      // 记录历史项
      addHistoryItem(timestamp);
    });
  })
  .catch(error => {
    console.error('读取 JSON 文件时发生错误:', error);
  });

// 折叠侧边栏按钮事件
document.querySelector("#btn-fold-in").addEventListener("click", () => {
  const sidebar = document.querySelector(".sidebar");
  sidebar.style.width = 0;
  const btnFoldOut = document.querySelector("#btn-fold-out");
  btnFoldOut.style.display = "inline-block";
});

// 发送按钮事件
document.querySelector("#input-send").addEventListener("click", () => {
  if (inputChat.value.trim() !== "") {
    sendRequest();
    inputChat.value = "";
  }
});

// 回车键发送消息事件
document.querySelector("#input-chat").addEventListener("keydown", (e) => {
  if (e.keyCode === 13 && inputChat.value.trim() !== "") {
    sendRequest();
    inputChat.value = "";
  }
});

// 展开侧边栏按钮事件
document.querySelector("#btn-fold-out").addEventListener("click", (e) => {
  const sidebar = document.querySelector(".sidebar");
  sidebar.style.width = "260px";
  e.target.style.display = "none";
});

// 新建会话按钮事件
document.querySelector("#new-session").addEventListener("click", () => {
  createNewSession();
});

// 滚动到最底部
function scrollToBottom() {
  resLog.scrollTop = resLog.scrollHeight;
}

// 新建会话函数
let recommendedQuestionsHtml = '';
function createNewSession() {
  // 保存 .recommended-questions 部分
  const recommendedQuestions = document.querySelector('.recommended-questions');
  if (recommendedQuestions) {
    recommendedQuestionsHtml = recommendedQuestions.outerHTML;
  }

  current_session_id = Date.now().toString(); // 生成新的 session_id
  sessions[current_session_id] = { name: "新会话", messages: [] }; // 初始化新的会话记录
  addHistoryItem(current_session_id); // 添加新的会话到历史栏

  // 清空聊天记录显示区域
  if (resLog) {
    resLog.innerHTML = '';
  }

  // 重新添加 .recommended-questions 部分
  if (resLog && recommendedQuestionsHtml) {
    resLog.innerHTML = recommendedQuestionsHtml;
  }
}

// 添加新的会话到历史栏
function addHistoryItem(session_id) {
  const sessionDiv = document.createElement("div");
  sessionDiv.className = "session-item";
  sessionDiv.dataset.id = session_id;
  sessionDiv.innerText = sessions[session_id].name;
  sessionDiv.addEventListener("click", () => {
    loadSession(session_id);
  });
  historyContainer.insertBefore(sessionDiv, historyContainer.firstChild);
}

// 更新会话名称
function updateHistoryName(session_id, name) {
  const sessionDiv = document.querySelector(`.session-item[data-id="${session_id}"]`);
  if (sessionDiv) {
    sessionDiv.innerText = name;
  }
}

// 加载会话
function loadSession(session_id) {
  current_session_id = session_id;
  resLog.innerHTML = '';
  const messages = sessions[session_id].messages;
  messages.forEach(msg => {
    if (msg.type === 'llm') {
      const llmMsg = document.createElement("div");
      const llmMsg_P = document.createElement("p");
      llmMsg.className = "llm-msg";
      llmMsg.appendChild(llmMsg_P);
      resLog.appendChild(llmMsg);
      llmMsg_P.innerText = msg.content;
    } else {
      const msgDiv = document.createElement("div");
      msgDiv.className = 'self-msg';
      msgDiv.innerText = msg.content;
      resLog.appendChild(msgDiv);
    }
  });
  scrollToBottom();
}

// 发送请求函数
function sendRequest() {
  const inputContent = document.querySelector("#input-chat").value;
  const data = {
    content: inputContent,
    userId: "zhangsan",
    a: "1000",
    session_id: current_session_id
  };

  // 显示用户发送的消息
  const selfMsg = document.createElement("div");
  selfMsg.innerText = data.content;
  selfMsg.className = "self-msg";
  resLog.appendChild(selfMsg);

  // 保存到当前会话记录
  if (sessions[current_session_id].messages.length === 0) {
    sessions[current_session_id].name = inputContent.length > 8 ? inputContent.substring(0, 8) : inputContent;
    updateHistoryName(current_session_id, sessions[current_session_id].name);
  }
  sessions[current_session_id].messages.push({ type: 'self', content: data.content });

  // 准备接收 LLM 消息的元素
  const llmMsg = document.createElement("div");
  const llmMsg_P = document.createElement("p");
  llmMsg.className = "llm-msg";
  llmMsg.appendChild(llmMsg_P);
  resLog.appendChild(llmMsg);

  // 滚动到底部
  scrollToBottom();

  // 发送 POST 请求
  fetch(`http://127.0.0.1:8000${uri}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data),
  })
    .then(response => {
      if (response.ok) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        const res = llmMsg_P;

        let accumulatedContent = '';
        function read() {
          reader.read().then(({ done, value }) => {
            if (done) {
              sessions[current_session_id].messages.push({ type: 'llm', content: accumulatedContent });
              accumulatedContent = '';
              console.log('Stream closed');
              return;
            }

            const chunk = decoder.decode(value, { stream: true });
            chunk.split('\r\n').forEach(eventString => {
              if (eventString) {
                res.innerHTML += eventString.replace(/\n/g, '<br>');
                accumulatedContent += eventString;
              }
            });

            read();
          }).catch(error => {
            console.error('Stream error', error);
          });
        }

        scrollToBottom();
        read();
      } else {
        console.error('Network response was not ok.');
      }
    })
    .catch(error => {
      console.error('Fetch error:', error);
    });
}

// 绑定下拉选择器更改事件，根据选择的选项更新 URI
const selectLLM = document.getElementById('selectLLM');
selectLLM.addEventListener('change', function() {
  const selectedOption = this.options[this.selectedIndex];
  console.log('Selected option:', selectedOption.value);
  uri = `/api/${selectedOption.value}`;
});

function fillInput(question) {
  const inputChat = document.getElementById('input-chat');
  inputChat.value = question;
  sendRequest();
  inputChat.value = "";
}

document.addEventListener('DOMContentLoaded', function() {
  const resLog = document.getElementById('res-log');
  const anchor = document.getElementById('scroll-anchor');

  function scrollToBottom() {
    resLog.scrollTop = resLog.scrollHeight;
  }

  const observer = new MutationObserver(function(mutationsList) {
    scrollToBottom();
  });

  const config = { childList: true, subtree: true };
  observer.observe(resLog, config);
  scrollToBottom();
});

document.addEventListener('DOMContentLoaded', function() {
  var toggleButton = document.getElementById('toggle-sidebar');
  var sidebar = document.querySelector('.footer-sidebar');
  toggleButton.addEventListener('click', function() {
    sidebar.classList.toggle('show');
  });
});
