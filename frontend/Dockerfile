# ============================================================
# FlightPulse frontend image — multi-stage.
# Stage 1 builds the React app; stage 2 serves it with Nginx,
# which also reverse-proxies /api and /admin to the Django web service.
# ============================================================

# --- Stage 1: build the React bundle ---
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# --- Stage 2: serve static build + act as reverse proxy ---
FROM nginx:1.27-alpine
# Replace the default site with our proxy config
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Copy the compiled assets
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
