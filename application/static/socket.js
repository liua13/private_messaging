$(document).ready(() => {
  const domain = "http://localhost:5000";
  const messagesSocket = io(`${domain}/messages`);
  //   $("#send_username").on("click", () => {
  //     privateSocket.emit("username", $("#username").val());
  //   });

  //   $("#send_private_message").on("click", () => {
  //     const recipient = $("#send_to_username").val();
  //     const message_to_send = $("#private_message").val();
  //     privateSocket.emit("private_message", {
  //       username: recipient,
  //       message: message_to_send,
  //     });
  //   });

  messagesSocket.on("privateChat", (msg) => {
    alert(msg);
  });
});
