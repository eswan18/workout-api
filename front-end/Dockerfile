# Largely taken from https://mherman.org/blog/dockerizing-a-react-app/

FROM node:12.2.0

WORKDIR /app

ENV PATH /app/node_modules/.bin:$PATH

COPY package.json /app/package.json
RUN npm install
RUN npm install react-scripts@3.0.1 -g

COPY ./public /app/public
COPY ./src /app/src

CMD ["npm", "start"]
