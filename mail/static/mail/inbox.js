// Ejecutamos todas las funciones luego de cargar el DOM
document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  
  // By default, load the inbox
  load_mailbox('inbox');

  // Configuramos cómo se envia un nuevo correo electrónico.
  document.querySelector('form').onsubmit = () => {
    send_email();
    setTimeout(load_mailbox('sent'), 8000);
    return false;
  };

  // Configuramos como abrir mails.
  document.addEventListener('click', event => {
    const element = event.target;
    if (element.className == 'conta' || element.className == 'row' || element.className == 'from' || element.className == 'subject' || element.className == 'timestamp') {
      open_email(element);
    }
  });

  // Configuramos como archivar y desarchivar emails.
  document.addEventListener('click', event => {
    const element = event.target;
    if (element.id === 'botonarch' || element.id === 'botondis' || element.id === 'botondis2' || element.id === 'botonarch2') {
          element.parentElement.remove();
          const email_id = element.dataset.page;
          archive(email_id, element.id);
          setTimeout(load_mailbox('inbox'), 8000);
    }
  });

  // Configuramos como responder los mails.
  document.addEventListener('click', event => {
    const element = event.target;
    if (element.id == 'reply') {
      const email_id = element.dataset.page;
      reply(email_id);
    }
  });

});


// Crear un nuevo email
function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#one-email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}


// Enviar mail
function send_email() {
  const recipients = document.querySelector('#compose-recipients').value;
  const subject = document.querySelector('#compose-subject').value;
  const body = document.querySelector('#compose-body').value;

  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
        recipients: recipients,
        subject: subject,
        body: body,
        read: false,
    })
  })
  .then(response => response.json())
  .then(result => {
      // Print result
      console.log(result);
  });
}


// Creamos la función para responder a los mails.
function reply(element) {

  console.log(element)
  // Buscamos la información del mail que nos interesa.
  fetch(`/emails/${element}`)
  .then(response => response.json())
  .then(email => {
    console.log(email)
    // Show compose view and hide other views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#one-email-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'block';

    // Completamos los campos
    document.querySelector('#compose-recipients').value = `${email.sender}`;
    document.querySelector('#compose-subject').value = `Re: ${email.subject}`;
    document.querySelector('#compose-body').value = `

--------------------------------------------------------
On ${email.timestamp} ${email.sender} wrote:
    
${email.body}`;

  });
}


// Abrir un mail
function open_email(element) {
  
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#one-email-view').style.display = 'block';
  
  // Limpiamos los mails abiertos anteriormente.
  document.querySelectorAll('#one-mail, #body, #botondis2').forEach(row => {
    row.remove();
  });

  // Buscamos la información del mail que nos interesa.
  fetch(`/emails/${element.id}`)
  .then(response => response.json())
  .then(email => {
    // Print email.
    console.log(email);
    // Creamos el mail que vamos a desplegar.
    const post = document.createElement('div');
    post.className = 'container p-3 my-3 border';
    post.id = 'one-mail';
    post.innerHTML = `<div id="subj">${email.subject}</div>
    <div id="send"><b>From:</b> ${email.sender}</div>
    <div id="recipi"><b>To:</b> ${email.recipients}</div>
    <div id="time" >${email.timestamp}</div>
    <button id="reply" name="reply" data-page="${email.id}" class="btn btn-primary">Reply</button></div>`
    console.log(email.user)
    if (email.user != email.sender) {
      if (email.archived == true) {
        post.innerHTML += `<button id="botondis2" name="botondis2" data-page="${email.id}" class="btn btn-primary">Unarchive</button>`
      } else {
        post.innerHTML += `<button id="botonarch2" name="botonarch2" data-page="${email.id}" class="btn btn-primary">Archive</button>`
      }
    }
    document.querySelector('#one-email-view').append(post);

    

    const poste = document.createElement('div');
    poste.id = 'body';
    poste.className = 'container p-3 my-3 border'
    poste.innerHTML = '';
    for (let x = 0; x < email.body.length; x++) {
      poste.innerHTML += `${email.body[x]}`;
      if (email.body[x] == '\n') {
        poste.innerHTML += '</p><p>';
      }
    }
    document.querySelector('#one-email-view').append(poste);

    // Marcamos como leido el mail.
    fetch(`/emails/${element.id}`, {
      method: 'PUT',
      body: JSON.stringify({
          read: true
      })
    })

});
}


// Cargar un buzón
function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#one-email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;


  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
      // Print emails
      console.log(emails);
      // ... do something else with emails ...
      emails.forEach(e => add_email(e, mailbox));  
  });

}


// Agregar mails al buzón
function add_email (email, mailbox) {

  const post = document.createElement('div');
  console.log(mailbox);
  post.className = 'conta';
  post.id = email.id;
  // Si es INBOX:
  if (mailbox == 'inbox') {
    post.innerHTML = `<div class="row"><div class="col-sm-6 col-md-7 col-lg-9"><div id="${email.id}" class="from">${email.sender}</div></div>
    <div class="col-sm-6 col-md-4 col-lg-3"><div id="${email.id}" class="timestamp">${email.timestamp}</div></div></div>
    <div class="row"><div class="col-sm-6 col-md-7 col-lg-9"><div id="${email.id}" class="subject">Subject: ${email.subject}</div></div>
    <div class="col-sm-2 col-md-2 col-lg-2"><button id="botonarch" name="botonarch" data-page="${email.id}" class="btn btn-primary">Archive</button></div></div>`;

    // Si es SENT:
  } else if (mailbox == 'sent') {
    post.innerHTML = `<div class="row"><div class="col-sm-6 col-md-7 col-lg-9"><div id="${email.id}" class="from">${email.recipients}</div></div>
    <div class="col-sm-6 col-md-4 col-lg-3"><div id="${email.id}" class="timestamp">${email.timestamp}</div></div></div>
    <div class="row"><div class="col-sm-6 col-md-7 col-lg-9"><div id="${email.id}" class="subject">Subject: ${email.subject}</div></div></div>`;

    // Si es ARCHIVE:
  } else if (mailbox == 'archive') {
    post.innerHTML = `<div class="row"><div class="col-sm-6 col-md-7 col-lg-9"><div id="${email.id}" class="from">${email.sender}</div></div>
    <div class="col-sm-6 col-md-4 col-lg-3"><div id="${email.id}" class="timestamp">${email.timestamp}</div></div></div>
    <div class="row"><div class="col-sm-6 col-md-7 col-lg-9"><div id="${email.id}" class="subject">Subject: ${email.subject}</div></div>
    <div class="col-sm-2 col-md-2 col-lg-2"><button id="botondis" name="botondis" data-page="${email.id}" class="btn btn-primary">Unarchive</button></div></div>`;
  }
  
  // Cambiamos el color si el mail está sin leer
  if (!email.read) {
  post.style.backgroundColor = 'White';
  }

  // Agregamos post a DOM
  document.querySelector('#emails-view').append(post);

}



function archive(email_id, archdis) {
  if (archdis == 'botonarch' || archdis == 'botonarch2') {
    fetch(`/emails/${email_id}`, {
      method: 'PUT',
      body: JSON.stringify({
          archived: true
      })
    })
    console.log("Email was archived")
  } else if (archdis == 'botondis' || archdis == 'botondis2') {
    fetch(`/emails/${email_id}`, {
      method: 'PUT',
      body: JSON.stringify({
          archived: false
      })
    })
    console.log("Email was disarchived")
  }
}