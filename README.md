# tickets
hardware tickets
docker build -t tickets .
docker run -d --restart always --name tickets -p 5555:80 tickets