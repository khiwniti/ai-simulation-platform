FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY apps/frontend/package*.json ./apps/frontend/
COPY packages/shared/package*.json ./packages/shared/

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build shared package
RUN npm run build --workspace=@ai-jupyter/shared

# Expose port
EXPOSE 3000

# Start development server
CMD ["npm", "run", "dev", "--workspace=@ai-jupyter/frontend"]