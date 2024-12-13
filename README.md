![14](https://user-images.githubusercontent.com/53878118/123514781-dd39f900-d694-11eb-9f7c-5a0dcbbcc045.jpg)

# Site-voyance

docker run -d --name pg_vector -e POSTGRES_DB=sitevoyance -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=bcxau9p^^123. -p 5432:5432 pgvector/pgvector:pg17

Site codé en Python DJANGO, AJAX , et Javascript.
Site en production sur la vm cloud sur <http://nunomars-server.eddi.cloud>!

# Project Infrastructure

Welcome to the infrastructure documentation for our project! 🚀 This guide provides an overview of the robust and scalable architecture we've implemented to power our application. From containerized services to a secure firewall setup, we've designed an environment that ensures reliability, performance, and maintainability.

## Key Components

- **LXD Containers**: Leverage the power of Linux containers for isolated and efficient deployment. Our containers include app servers, a load balancer, a PostgreSQL database, a DNS server, and a firewall to control traffic.

- **Load Balancer (Nginx)**: Distribute incoming traffic across multiple app servers, ensuring high availability and optimal performance. Nginx acts as a reverse proxy, seamlessly routing requests to the appropriate backend services.

- **Database (PostgreSQL)**: Store and manage data with the robust PostgreSQL database. Our setup includes secure configurations, remote access, and efficient data handling.

- **DNS Server (BIND9)**: Facilitate domain resolution within our network. BIND9 is configured to handle local zones, providing efficient and reliable DNS services.

- **Firewall (iptables)**: Secure our infrastructure with a finely tuned firewall. Control incoming traffic, allowing only essential connections to pass through and safeguarding our environment.

## Deployment Workflow

Our deployment workflow automates the setup and configuration of each component. Using GitHub Actions, create a Docker image, configure services, and deploy our application seamlessly. The workflow ensures consistency and repeatability in our deployment process.

## Getting Started

Whether you're a new contributor or setting up the project locally, the documentation provides step-by-step instructions to replicate our infrastructure. Dive in and explore the architecture that powers our application.

Feel free to reach out if you have any questions or suggestions. Happy coding! 🚀

