# tickets
hardware tickets <br/>
docker build -t tickets . <br/>
docker run -d --restart always --name tickets -p 443:5556 tickets
