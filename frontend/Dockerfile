FROM node:20-alpine

WORKDIR /app

# Copiar archivos de dependencias primero (mejor cache)
COPY package.json package-lock.json* ./

# Instalar dependencias
RUN npm install

# Copiar el resto del código
COPY . .

EXPOSE 5173

# Iniciar Vite en modo dev, escuchando en todas las interfaces
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
