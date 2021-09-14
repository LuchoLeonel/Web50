// Ejecutamos todas las funciones luego de cargar el DOM
document.addEventListener('DOMContentLoaded', function() {

    // Configuramos como archivar y desarchivar emails.
    document.addEventListener('click', event => {
        const element = event.target;

        if (element.className == 'edit') {
            console.log(element.id)  
            editar(element.id) 
            }

        if (element.id == 'save-edit') {
            console.log(element.id)  
            guardar(element.parentElement.id)
            }

        if (element.className == 'unlike') {
            console.log(element.id)  
            like(element.id)
            }

        if (element.className == 'imagen') {
            console.log(element.id)
            unlike(element.id)
            }
        
        if (element.id == 'follow') {
            console.log(element.parentElement.id)
            follow(element.parentElement.id)
            }
        
        if (element.id == 'unfollow') {
            console.log(element.parentElement.id)
            unfollow(element.parentElement.id)
            }
        
        if (element.id == 'comments') {
            console.log(element.className)
            comentarios(element.className)
            }
        
        if (element.id == 'no-comments') {
            console.log(element.className)
            no_comentarios(element.className)
            }

        if (element.id == 'save-comment') {
            console.log(element.parentElement.id)  
            guardar_comentario(element.parentElement.id)
            }

    });

    check_likes()
    
    document.querySelectorAll('.edit-view').forEach(row => {
        row.style.display = 'none';
        });
    
    document.querySelectorAll('#comentar').forEach(row => {
        row.style.display = 'none';
        });

    setInterval(actualizar_todos_los_likes, 60000);

});


function editar(id) {
    
    document.querySelectorAll('.content-view, .edit').forEach(content => {
        if (content.id == `${id}`) {
            content.style.display = 'none';
            document.querySelectorAll('.edit-view').forEach(edit => {
                if (edit.id == `${id}`) {
                    edit.style.display = 'block';
                    fetch(`/post/${id}`)
                    .then(response => response.json())
                    .then(post => {
                        document.querySelectorAll('.area-edit'). forEach( rellenar => {
                            if (rellenar.id == `${id}`) {
                                rellenar.value = `${post.content}`;
                            }
                        })
                    });
                } else {
                    edit.style.display = 'none';
                }
            });
        }
    });
    
    
};
    

function guardar(id) {
    document.querySelectorAll('.area-edit').forEach(post => {
        if (post.id == `${id}`) {
            const edicion = post.value
            console.log(post.value)
            fetch(`/post/${id}`, {
                method: 'PUT',
                body: JSON.stringify({
                    content: edicion,
                    })
                });
            console.log("Se guardó")  
            document.querySelectorAll('.content-view, .edit').forEach(content => {
                if (content.id == `${id}`) {
                    content.style.display = 'block';
                    if (content.className == 'content-view') {
                        content.innerHTML = `<p style="margin-left: 15px; margin-top: 0px; "id="texto">${edicion}</p>`
                        }   
                }
            });
            document.querySelectorAll('.edit-view').forEach(edit => {
                if (edit.id == `${id}`) {
                    edit.style.display = 'none';
                }
            });
        }
    });
}


function follow(user) {
    fetch(`/follow/${user}`, {
        method: 'POST',
        body: JSON.stringify({
            action: "follow"
        })
    });
    parent = document.querySelector('#follow').parentElement
    parent.innerHTML = `<input id="unfollow" class="btn btn-primary" name="unfollow" type="submit" value="Unfollow">`
    let i = document.querySelector('#seguidores').innerHTML;
    i++;
    document.querySelector('#seguidores').innerHTML = i;
}

function unfollow(user) {
    fetch(`/follow/${user}`, {
        method: 'POST',
        body: JSON.stringify({
            action: "unfollow"
        })
    });
    parent = document.querySelector('#unfollow').parentElement
    parent.innerHTML = `<input id="follow" class="btn btn-primary" name="follow" type="submit" value="Follow">`
    let i = document.querySelector('#seguidores').innerHTML;
    i--;
    document.querySelector('#seguidores').innerHTML = i;
}


function like(id) {
    document.querySelectorAll('.unlike').forEach(post => {
        if (post.id == `${id}`) {
            fetch(`/like/${id}`, {
                method: 'POST',
                body: JSON.stringify({
                    action: "like"
                })
                });
            
            document.querySelectorAll('#imagen').forEach(img => {
            if (img.className == `${id}`) {    
                img.style.display = 'block';
                let i = img.lastChild.innerHTML;
                i++;
                console.log(i)
                img.lastChild.innerHTML = ` ${i}`
                }
            });
            document.querySelectorAll('#unlike').forEach(img => {
                if (img.className == `${id}`) {    
                    img.style.display = 'none';
                    let i = img.lastChild.innerHTML;
                    i++;
                    img.lastChild.innerHTML = ` ${i}`
                    }
            });
        }
    });
}


function unlike(id) {
    document.querySelectorAll('.imagen').forEach(post => {
        if (post.id == `${id}`) {
            fetch(`/like/${id}`, {
                method: 'POST',
                body: JSON.stringify({
                action: "unlike"
            })
                });
            
            document.querySelectorAll('#unlike').forEach(img => {
            if (img.className == `${id}`) {    
                img.style.display = 'block';
                let i = img.lastChild.innerHTML;
                i--;
                img.lastChild.innerHTML = ` ${i}`
                }
            });
            document.querySelectorAll('#imagen').forEach(img => {
                if (img.className == `${id}`) {    
                    img.style.display = 'none';
                    let i = img.lastChild.innerHTML;
                    i--;
                    console.log(i)
                    img.lastChild.innerHTML = ` ${i}`
                    }
            });
        }
    });
}


function check_likes() {
    document.querySelectorAll('#imagen, #unlike').forEach(img => {
        let id = img.className
        fetch(`/likes/${id}`, {
            method: 'GET',
        })
        .then(response => response.text())
        .then(likes => {
        if (likes == 'True' && img.id == 'unlike') {
            img.style.display = 'none';
        } else if (likes == 'False' && img.id == 'imagen') {
            img.style.display = 'none';
        }
        });
});
}


function actualizar_todos_los_likes () {
    document.querySelectorAll('#imagen, #unlike').forEach(img => {
        let id = img.className
        fetch(`/like/${id}`, {
            method: 'GET',
        })
        .then(response => response.text())
        .then(likes => {
            document.querySelectorAll(`#numero`).forEach(post => {
                if (post.parentElement.className == `${id}`) {
                    post.innerHTML = ` ${likes}`
                }
            });
        });
    });
}

function comentarios(id) {
    fetch(`/comments/${id}`, {
        method: 'GET',
    })
    .then(response => response.json())
    .then(comments => {
        for (let i = 0; i < comments.length; i++){
            const post = document.createElement('div');
            post.className = 'container p-3 my-3 border';
            post.id = `${id}`;
            post.innerHTML = `<a><b>${comments[i].user}:</b></a>
            <p style="margin-left: 15px;">${comments[i].comment}</p>`
            
            document.querySelectorAll('#comentarios').forEach(comentar => {
                if (comentar.className == `${id}`) {
                    comentar.append(post);
                }
                else {
                    comentar.innerHTML = ''
                }
            }); 
        }
        if (comments.length == 0) {
            document.querySelectorAll('#comentarios').forEach(comentar => {
                if (comentar.className == `${id}`) {
                    comentar.append("No comments");
                }
            }); 
        }
        document.querySelectorAll('#comentar').forEach(comentar => {
            if (comentar.className == `${id}`) {
                comentar.style.display = 'block'
            }
            else {
                comentar.style.display = 'none'
            }
        });

        document.querySelectorAll('.area-comment').forEach(post => {
            post.value = '';
        });

        document.querySelectorAll('#comments').forEach(comment => {
            if (comment.className == `${id}`) {
                comment.id = 'no-comments'
            }
        });
    });
}

function no_comentarios(id) {
    document.querySelectorAll('#comentarios').forEach(comentar => {
        if (comentar.className == `${id}`) {
            comentar.innerHTML = ''
        }
    });

    document.querySelectorAll('#comentar').forEach(comentar => {
        if (comentar.className == `${id}`) {
            comentar.style.display = 'none'
        }
    });

    document.querySelectorAll('#no-comments').forEach(comment => {
        if (comment.className == `${id}`) {
            comment.id = 'comments'
        }
    });

}

function guardar_comentario(id) {
    console.log(id)
    document.querySelectorAll('.area-comment').forEach(postear => {
        if (postear.id == `${id}`) {
            const edicion = postear.value
            fetch(`/comments/${id}`, {
                method: 'POST',
                    body: JSON.stringify({
                    comment: edicion
                })
            });
            if (edicion != '') {
                const post = document.createElement('div');
                post.className = 'container p-3 my-3 border';
                post.id = `${id}`;
                post.innerHTML = `<a><b>New Comment:</b></a>
                <p style="margin-left: 15px;">${postear.value}</p>`
                
                document.querySelectorAll('#comentarios').forEach(comentar => {
                    if (comentar.className == `${id}`) {
                        comentar.append(post);
                    }
                });
            }
            document.querySelectorAll('.area-comment').forEach(post => {
                post.value = '';
            });
        }
    });
}