# Stage 1: Build the Next.js application
FROM node:18-alpine AS builder

WORKDIR /app

# Install glibc for Next.js SWC compatibility on Alpine
RUN apk add --no-cache libc6-compat

COPY package.json package-lock.json ./
RUN npm install

COPY . ./

# Environment variables for build time (if any, e.g., NEXT_PUBLIC_*)
# For now, assuming no specific build-time env vars are needed beyond what's in .env.local if any
# RUN npm run build will pick them up from the environment if set, or from .env.production.local if present

RUN npm run build

# Stage 2: Serve the application with a lightweight server
FROM node:18-alpine AS runner

WORKDIR /app

# Set environment variables for runtime
ENV NODE_ENV=production
# Copy only necessary files from the build stage
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/public ./public
# COPY --from=builder /app/.env.local ./.env.local # Copy .env.local for runtime environment variables

EXPOSE 3000

CMD ["npm", "run", "start"]
