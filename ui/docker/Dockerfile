FROM node:18.17.0-slim as build

WORKDIR /ui

COPY . .

RUN npm install && \
    npm run build

FROM nginx:latest

COPY --from=build /ui/dist /usr/share/nginx/html/

EXPOSE 80
