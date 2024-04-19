<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>

  <h1>MapSyncer Docker Setup and Usage</h1>

  <p>This repository contains the necessary setup for using MapSyncer within a Docker environment. </p>

  <h2>Prerequisites</h2>
  <ul>
    <li><a href="https://www.docker.com/" target="_blank">Docker</a></li>
    <li><a href="https://docs.docker.com/compose/" target="_blank">Docker Compose</a></li>
  </ul>

  <h2>Getting Started</h2>
  <ol>
    <li>Clone the repository:</li>
  </ol>

  <pre><code>git clone https://github.com/mapilio/mapsyncer
cd mapsyncer/docker</code></pre>

  <ol start="2">
    <li>Build the Docker image:</li>
  </ol>

  <pre><code>docker compose up -d  --build</code></pre>


  <h2>MapSyncer Command</h2>

  <strong>To run MapSyncer in one line:</strong>

  <pre><code>sudo docker exec -it mapsyncer RunMapSyncer</code></pre>
  <p><b>After this command, Docker will start MapSyncer and redirect to a web page on your localhost. You will be redirected to the web page by clicking on the host address https://127.0.0.1:5050. If you don't get redirected after clicking, you can copy the address and paste it into the URL section of your browser.</b></p>
  
  <h2>Important Note</h2>
  <p>
    When accessing the provided address, you may encounter a security warning stating <b>"Your connection is not private"</b> in your web browser. To proceed, please click the <b>"Advanced"</b> button and select the option to continue to the site. This warning is due to the SSL certificate currently being in the process of approval and will be validated shortly.
  </p>

</body>
</html>
