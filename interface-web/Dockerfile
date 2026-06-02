FROM node:20-alpine

WORKDIR /app

COPY interface-web/package*.json /app/
RUN npm ci

COPY interface-web /app

EXPOSE 8080

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "8080"]
