FROM node:20-alpine
WORKDIR /app

COPY package.json ./
RUN npm install --production=false

COPY . .

# Build during image creation
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
