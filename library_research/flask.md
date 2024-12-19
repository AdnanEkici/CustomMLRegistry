## Flask

Flask is a lightweight, micro web framework for Python, designed for simplicity and ease of use.

### Key Features of Flask

1. **Minimalist Framework**:
   - A micro-framework with minimal dependencies, making it lightweight and easy to get started with.

2. **Extensible**:
   - Highly customizable and flexible, allowing developers to add only the components they need through extensions.

3. **Routing and Middleware**:
   - Simple and intuitive URL routing system, enabling developers to easily map URLs to functions.
   - Supports middleware for request processing and response handling.

4. **Templating**:
   - Utilizes Jinja2 templating engine for creating dynamic HTML pages.

5. **Built-in Development Server**:
   - Comes with a built-in development server and debugger, simplifying the development process.

6. **Large Ecosystem**:
   - Strong community support and a rich ecosystem of extensions and libraries.

### Pros

1. **Lightweight and Flexible**:
   - Simple to set up and use for small to medium-sized applications.

2. **Extensive Documentation**:
   - Comprehensive documentation and a large number of tutorials available.

3. **Rich Ecosystem**:
   - Many available plugins and extensions for various functionalities (e.g., authentication, databases).

4. **Simple Learning Curve**:
   - Easy for beginners due to its straightforward design and API.

### Cons

1. **Not Suitable for Large Applications**:
   - Lacks some advanced features needed for large-scale applications out of the box.

2. **Single-Threaded**:
   - By default, Flask runs in a single thread, which may limit performance under heavy load.

3. **Manual Configuration Required**:
   - Often requires manual setup and configuration for more complex use cases.

4. **Limited Built-in Tools**:
   - Fewer built-in features compared to more extensive frameworks like Django.

## FastAPI

FastAPI is a modern, fast (high-performance) web framework for building APIs with Python, based on standard Python type hints.

### Key Features of FastAPI

1. **High Performance**:
   - Built on top of Starlette for the web parts and Pydantic for data handling, enabling high performance close to Node.js and Go.

2. **Automatic Interactive API Documentation**:
   - Automatically generates interactive API documentation using OpenAPI and JSON Schema standards, available via Swagger UI and ReDoc.

3. **Type Hints and Data Validation**:
   - Uses Python type hints to automatically validate request data, ensuring robust and error-free code.

4. **Asynchronous Programming**:
   - Supports asynchronous programming with `async` and `await`, making it easy to build fast, non-blocking APIs.

5. **Dependency Injection**:
   - Provides a powerful dependency injection system for managing application dependencies in a clean and modular way.

6. **Built-in Security and Authentication**:
   - Includes utilities for handling security, OAuth2, JWT token-based authentication, and more.

### Pros

1. **Fast and Efficient**:
   - High performance due to asynchronous support and optimized code, suitable for handling many requests per second.

2. **Automatic API Documentation**:
   - Generates user-friendly API documentation with minimal setup, saving development time.

3. **Type Safety**:
   - Strong typing support helps catch errors early and improves code maintainability.

4. **Modern Python Features**:
   - Leverages modern Python features, such as type hints and `async`/`await`, making the code more readable and efficient.

5. **Built for APIs**:
   - Specifically designed for building APIs, with robust handling of JSON, data validation, and error management.

### Cons

1. **Learning Curve for Beginners**:
   - Although well-documented, the use of modern Python features and asynchronous programming may present a learning curve for some developers.

2. **Smaller Ecosystem**:
   - Compared to older frameworks like Flask or Django, FastAPI has a smaller ecosystem and fewer extensions.

3. **Rapid Changes**:
   - Being relatively new, FastAPI is rapidly evolving, which may lead to breaking changes and less stable third-party libraries.

4. **Community Support**:
   - While growing fast, the community is still smaller compared to more established frameworks like Flask or Django.


## Flask vs FastAPI Comparison

| Feature                                 | **Flask**                                                                 | **FastAPI**                                                           |
|-----------------------------------------|--------------------------------------------------------------------------|----------------------------------------------------------------------|
| **Framework Type**                      | Micro-framework                                                          | Modern, high-performance web framework                               |
| **Performance**                         | Single-threaded, slower under heavy load                                 | High performance, supports asynchronous programming                  |
| **Ease of Use**                         | Simple and beginner-friendly                                             | Easy to use but can have a learning curve with type hints and async  |
| **Documentation**                       | Extensive documentation and tutorials                                    | Excellent documentation with auto-generated API docs (Swagger, ReDoc)|
| **Community and Ecosystem**             | Large community with a rich ecosystem of plugins and extensions          | Growing community with a smaller but rapidly expanding ecosystem     |
| **Data Validation**                     | Manual validation using libraries like Marshmallow or custom validation  | Automatic data validation using Python type hints and Pydantic       |
| **API Documentation**                   | No automatic API documentation; requires third-party libraries           | Automatic interactive API documentation with OpenAPI standards       |
| **Built-in Features**                   | Minimal built-in features; highly extensible                             | Built-in dependency injection, OAuth2, JWT, and more                 |
| **Development Speed**                   | Quick to set up and start for small projects                             | Fast to build and deploy APIs due to built-in features               |
| **Best For**                            | Simple applications, prototyping, and learning                           | Building fast APIs, production-ready microservices, modern Python projects |
| **Data Handling**                       | Uses libraries like Marshmallow or custom validation                     | Uses Pydantic for data validation and parsing                        |
| **Concurrency Support**                 | Single-threaded; requires libraries like Gevent or Asyncio for async     | Native `async`/`await` support, highly optimized for concurrency     |
| **Security**                            | Requires third-party libraries for security features                     | Built-in support for handling security, including OAuth2 and JWT      |
| **Flexibility**                         | Highly flexible, with numerous extensions available                      | Flexible but more opinionated in handling requests and responses     |
| **Learning Curve**                      | Low, especially for beginners familiar with Python                       | Moderate, especially with asynchronous programming and type hints    |
| **Deployment**                          | Easy to deploy, with various hosting options                             | Optimized for modern deployment, including Docker and Kubernetes     |
| **Maturity**                            | Over a decade old with proven stability                                  | Relatively new but rapidly gaining popularity                        |

## Decisions

For the model registry;

While FastAPI offers superior scalability and performance, I am opting for Flask due to time constraints and familiarity. To enhance scalability, I will use Flask-Executor to efficiently manage background tasks.

In Flask-Executor, I will select ProcessPoolExecutor because it allows for true parallelism, making it ideal for CPU-bound tasks such as model training or heavy data processing. Unlike ThreadPoolExecutor, which is limited by Python's Global Interpreter Lock (GIL), ProcessPoolExecutor can run multiple processes concurrently, maximizing CPU utilization and improving performance for computationally intensive operations.

For inference server;

For the inference server, the priority is to ensure high speed, scalability, and the ability to handle a large number of requests efficiently, especially since it involves fewer routes than a model registry. Therefore, I have chosen FastAPI, which is well-suited for high-performance use cases due to its asynchronous capabilities and modern design.