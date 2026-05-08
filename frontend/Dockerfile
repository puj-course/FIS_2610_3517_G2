# ---- Etapa 1: Construcción (Build) ----
FROM node:20-alpine AS builder

WORKDIR /app


COPY package*.json ./


RUN npm ci


COPY . .


RUN npm run build



FROM nginx:alpine


COPY --from=builder /app/dist /usr/share/nginx/html


RUN echo 'server { \
    listen 80; \
    \
    # Servir la aplicación de React \
    location / { \
        root /usr/share/nginx/html; \
        index index.html; \
        try_files $uri $uri/ /index.html; \
    } \
    \
    # Proxy para enviar las peticiones de API al contenedor del backend \
    location /api/ { \
        proxy_pass http://backend:8000/; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Nginx escucha por defecto en el puerto 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
