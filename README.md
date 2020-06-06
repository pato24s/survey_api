## Introducción:
La aplicación fue pensada como una página en la que los usuarios registrados pueden crear encuestas. 
Los endpoints que tienen el método POST fueron pensados para ser llamados desde un frontend en el que el usuario en cuestión complete un form con los datos necesarios.

Las encuestas son simplemente tópicos de los que se desea generar preguntas. Por ejemplo una encuesta vacía recién generada podría constar simplemente de un título (Ej: 'Encuesta sobre alimentación') y una serie de tags (Ej: alimentación, comida, gastronomía).

Una vez generada la encuesta, los usuarios (ya sea el creador de la encuesta u otros) pueden agregar preguntas y sus respectivas posibles respuestas. Como por ejemplo:
Pregunta: 'Probaste el producto X?'
Posibles respuestas: 'Sí', 'No'

Cuando la encuesta tiene preguntas cualquier usuario, no hace falta estar registrado, puede contestarla. Sus respuestas para cada pregunta son guardadas en la base de datos, permitiendo que finalmente se pueda acceder a los resultados de la misma.

## Desafíos encontrados:

El primer gran desafío fue pensar un modelo que cumplan con los requisitos del dueño del producto, esto lo hice pensando a su vez en el modelo relacional vinculado a este. Esta fue de las tareas que más tiempo me llevó, dado que le dediqué el primer fin de semana. 
Una vez pensado un modelo que parecía satisfacer las condiciones pedidas, otro desafío fue aplicar esto a python. Ya que si bien es un lenguaje que conozco, lo utilicé relativamente poco y para realizar pequeños proyectos personales. Investigar bien sobre flask, sqlalchemy, como conectar esto con una base de datos de postgres, fue un muy interesante desafío.
El desafío final, al que me hubiese gustado poder dedicarle más tiempo, fue dockerizar el proyecto. Nunca lo había hecho, por lo que siempre consideré a docker como una caja negra. Si bien por cuestiones de tiempo no llegué a dockerizarlo correctamente, siento que aprendí mucho en el proceso y que ahora entiendo mucho más como funciona.

## Endpoints:

* **POST /api/users** : Utilizado para registrar usuarios en la aplicación. Se pensó para que se reciba data de un form en el que se obtiene username, email y contraseña del usuario en cuestión.

* **POST /api/surveys** : Utilizado para registrar usuarios en la aplicación. La data se obtiene de un form en el que se completa título de la encuesta, tags (opcionales) y fecha de vencimiento (opcional). Requiere que el usuario esté registrado en la aplicación.

* **POST /api/surveys/<survey_id>/questions** : Utilizado para agregar preguntas a una encuesta existente. Se imaginó un form en el que el usuario tiene un campo donde escribir el título de la pregunta y tiene cuatro campos para agregar preguntas, de los cuales puede completar entre 1 y 4. Requiere que el usuario esté registrado en la aplicación

* **POST /api/surveys/<survey_id>/submit_response** : Utilizado para responder una enceusta. Se pensó para que desde el front se envié una lista de tuplas (id de pregunta, id de respuesta) que representan todas las respuestas dadas por el usuario para dicha encuesta.

* **GET /api/users/<user_id>/questions** : Utilizado para obtener un listado de todas las preguntas creadas por cierto usuario.

* **GET /api/surveys** : Utilizado para obtener un listado de todas las encuestas del sistema, con sus respectivas preguntas y respuestas posibles.

* **GET /api/surveys/<survey_id>/results** : Utilizado para, dada una encuesta, conseguir los resultados de la misma. Es decir, para cada pregunta de la encuesta saber que porcentaje de elección tiene cada una de sus posibles respuestas. 

## Como ejecutar:
Dado que no pude dockerizar el proyecto, la forma de ejecutarlo sería la siguiente:

* Instalar las bibliotecas utilizadas:
    ```sh
    $ pip install -r requirements.txt
    ```

* Levantar la base de datos de postgres creándola a través de los modelos de flask
    ```sh
    $ flask db init
    ```
    ```sh
    $ flask db migrate
    ```
    ```sh
    $ flask db upgrade
    ```

* Ejecutar la aplicación
    ```sh
    $ flask run
    ```

## Trabajo pendiente:
  Dado que no pude dedicarle todo el tiempo que me hubiese gustado, quedaron varias cosas pendientes. 
  Entre ellas destaco:
  * Dockerizar correctamente (no logré que se inicialice la base de datos mediante los comandos de flask).
  * Reorganizar el código separándolo en distintos archivos. Ej: Uno para las rutas, otro para los modelos, etc.
  * Ampliar la suite de tests para obtener mucha más cobertura.
  * Agregar un frontend.
  * Investigar como agregar un cron para que elimine las encuestas según su fecha de expiración.
 

