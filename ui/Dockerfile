FROM node:18.17.0-slim as build

WORKDIR /ui

COPY . .

RUN npm install
RUN npm run build

FROM nginx:latest
# RUN apt-get update && \
#     apt-get install nginx -y && \
#     apt-get clean

# COPY --from=build /ui/dist /var/www/html/
COPY --from=build /ui/dist /usr/share/nginx/html/

EXPOSE 80
# CMD ["nginx", "-g", "daemon off;"]
