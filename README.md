# tickets
hardware tickets <br/>
docker build -t tickets . <br/>
docker run -d --restart always --name tickets -p 5555:80 tickets