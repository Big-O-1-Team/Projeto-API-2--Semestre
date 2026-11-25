FROM node:22-alpine AS mapas
RUN npm install --prefix /mapa --no-save --ignore-scripts leaflet@1.9.4

FROM nginx:alpine

COPY . /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=mapas /mapa/node_modules/leaflet/dist/ /opt/leaflet/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
