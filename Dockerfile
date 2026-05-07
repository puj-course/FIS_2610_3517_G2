# ============================================================
# OddsEngine — Frontend Dockerfile (multi-stage build)
# Etapa 1: Compilar la app con Node
# Etapa 2: Servir el build con nginx (más liviano que Node)
# ============================================================
 
# ---- Etapa 1: Build ----
FROM node:20-alpine AS builder
 
WORKDIR /app
 
# Copiar dependencias primero (aprovecha cache de Docker)
COPY package.json package-lock.json ./
 
# Instalar dependencias
RUN npm ci
 
# Copiar el resto del código fuente
COPY . .
 
# Compilar la aplicación para producción
RUN npm run build
 
# ---- Etapa 2: Servir con nginx ----
FROM nginx:alpine
 
# Copiar el build generado al directorio de nginx
COPY --from=builder /app/dist /usr/share/nginx/html
 
# Configuración de nginx para manejar rutas de React (SPA)
RUN echo 'server { \
    listen 80; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html; \
        try_files $uri $uri/ /index.html; \
    } \
    location /api/ { \
        proxy_pass http://backend:8000; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
    } \
}' > /etc/nginx/conf.d/default.conf
 
# Puerto en el que sirve nginx
EXPOSE 80
 
CMD ["nginx", "-g", "daemon off;"]
