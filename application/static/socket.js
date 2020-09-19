$(document).ready(() => {
  // to do: seen / not seen (database)
  // to do: show message + time instead of userID for chatContainer (for sender + database)
  // to do: send new message

  // Handover Protocol, One-Time Notifications, Private Replies, Quick Replies, and the Extension SDK.
  // https://fbmessaging3.devpost.com/?utm_source=devpost&utm_medium=newsletter

  const domain = "http://localhost:5000";
  const socket = io(`${domain}`);

  socket.on("connect", () => {
    socket.emit("userConnected");
  });

  socket.on("chatRooms", (chatRooms) => {
    $(".chatsContainer").html("");
    // chatRooms is array of dictionary {chatID, userID}
    for (const chatRoom of chatRooms) {
      const { chatID, userID, firstName, lastMessage } = chatRoom;
      createChat(chatID, userID, firstName, lastMessage);
    }
  });

  const createChat = (chatID, userID, firstName, lastMessage) => {
    const chatContainer = document.createElement("div");

    $(chatContainer)
      .addClass("chatContainer")
      .click(() => {
        changeChat(userID, chatID);
      });

    const changeChat = (userID, chatID) => {
      socket.emit("changeChat", userID, chatID);
      $("form[name='sendNewMessageForm']").css("display", "none");
      $("form[name='sendMessageForm']").css("display", "block");
      $("form[name='sendMessageForm'] > .recipientContainer > div").html(
        firstName
      );
      $(`.chatContainer[data-id="${chatID}"] .notificationDot`).css(
        "visibility",
        "hidden"
      );

      $("form[name='sendMessageForm']")
        .unbind("submit")
        .bind("submit", (event) => {
          event.preventDefault();
          socket.emit("message", {
            datetime: new Date().toISOString(),
            chatID: chatID,
            recipientID: userID,
            message: $("form[name='sendMessageForm'] #message").val(),
          });
          $("input[name='message']").val("");
        });
    };

    const notificationDot = document.createElement("div");
    $(notificationDot).addClass("notificationDot");

    const userDiv = document.createElement("span");
    $(userDiv).addClass("firstName").html(firstName);

    const dateDiv = document.createElement("span");
    $(dateDiv).addClass("datetime").html(convertDate(lastMessage["datetime"]));

    const recipientContainer = document.createElement("div");
    $(recipientContainer).append(userDiv).append(dateDiv);

    const messageText = document.createElement("div");
    $(messageText).addClass("message").html(lastMessage["message"]);

    const chatMessageContainer = document.createElement("div");
    $(chatMessageContainer)
      .append(recipientContainer)
      .append(messageText)
      .addClass("chatMessageContainer");

    $(chatContainer)
      .append(notificationDot)
      .append(chatMessageContainer)
      .attr("data-id", chatID);
    $(".chatsContainer").prepend(chatContainer);
  };

  // // if error
  // socket.on("sendMessageError", (errors) => {
  //   for (const className in errors) {
  //     let errorString = "";
  //     for (const error of errors[className]) {
  //       errorString += error;
  //     }
  //     $(`.${className}Error`).html(errorString);
  //   }
  // });

  socket.on("sentMessage", (data) => {
    const { message, datetime, chatID } = data;
    newMessage(chatID, datetime, message, "sentMessage");
  });

  socket.on("receivedMessage", (data) => {
    socket.emit("receivedMessage", data);
  });

  socket.on("displayReceivedMessage", (data) => {
    const { message, datetime, chatID } = data;
    newMessage(chatID, datetime, message, "receivedMessage");
  });

  const newMessage = (chatID, datetime, message, messageType) => {
    $(`.chatContainer[data-id="${chatID}"] .message`).html(message);
    displayMessage(datetime, message, messageType);
    $(".messagesContainer").scrollTop(
      $(".messagesContainer").prop("scrollHeight")
    );
  };

  socket.on("displayNotification", (data) => {
    const { senderID, chatID, firstName, message, datetime } = data;
    $(`.chatContainer[data-id="${chatID}"]`).remove();
    createChat(chatID, senderID, firstName, { message, datetime });
    $(`.chatContainer[data-id="${chatID}"] .notificationDot`).css(
      "visibility",
      "visible"
    );
  });

  socket.on("displayAllMessages", (allMessages) => {
    $(".messagesContainer").html("");
    for (const messageInfo of allMessages) {
      const { chatID, datetime, message, messageType } = messageInfo;
      displayMessage(datetime, message, messageType);
    }

    $(".messagesContainer").scrollTop(
      $(".messagesContainer").prop("scrollHeight")
    );
  });

  $("form[name='sendNewMessageForm']")
    .unbind("submit")
    .bind("submit", (event) => {
      event.preventDefault();
      const recipientEmail = $(
        "form[name='sendNewMessageForm'] #recipientID"
      ).val();
      const message = $("form[name='sendNewMessageForm'] #message").val();
      alert(recipientEmail + " " + message);
    });

  const displayMessage = (datetime, message, messageType) => {
    const date = convertDate(datetime);

    const messageContainer = document.createElement("div");
    $(messageContainer).addClass("messageContainer");

    const innerMessageContainer = document.createElement("div");
    $(innerMessageContainer).addClass(messageType);

    const messageDiv = document.createElement("div");
    $(messageDiv).html(message).addClass("message");

    const datetimeDiv = document.createElement("div");
    $(datetimeDiv).html(date).addClass("date");

    $(innerMessageContainer).append(messageDiv).append(datetimeDiv);
    $(messageContainer).append(innerMessageContainer);
    $(".messagesContainer").append(messageContainer);
  };

  const convertDate = (datetime) => {
    let date = moment.utc(datetime, "YYYY-MM-DD HH:mm:ss.SSS");
    date = new Date(date);
    date = `${date.toLocaleDateString()} ${date.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    })}`;
    return date;
  };
});
