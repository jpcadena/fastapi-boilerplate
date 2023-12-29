# fastapi-boilerplate

<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>

<!-- PROJECT SHIELDS -->
<!--
*** Markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
-->

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/othneildrew/Best-README-Template">
    <img src="assets/images/logo.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">Fastapi boilerplate</h3>

  <p align="center">
    Fastapi boilerplate
    <br />
    <a href="https://github.com/jpcadena/fastapi-boilerplate"><strong>Explore the docs »</strong></a>
    <br />
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
       <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#api-documentation">API Documentation</a></li>
    <li><a href="#openapi-typescript-codegen">OpenAPI TypeScript Codegen</a>
      <ul>
        <li><a href="#react-native-installation">React Native Installation</a></li>
        <li><a href="#codegen-usage">Codegen Usage</a></li>
      </ul>
    </li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#security">Security</a></li>
    <li><a href="#code-of-conduct">Code of Conduct</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About The Project

![Project][project-screenshot]

This backend project is FastAPI template. This project serves as the backend,
which aims to provide a robust and reliable system to its users. This
backend application plays a crucial role in providing the functionality for
user authentication, real-time monitoring, data processing, and advanced
alerting system. It is designed to ensure the scalability and
maintainability of the mobile app, making it a vital part of the overall
solution.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built with

[![Python][python-shield]][python-url] [![FastAPI][fastapi-shield]][fastapi-url] [![Pydantic][pydantic-shield]][pydantic-url] [![Starlette][starlette-shield]][starlette-url] [![Uvicorn][uvicorn-shield]][uvicorn-url] [![postgresql][postgresql-shield]][postgresql-url] [![Redis][redis-shield]][redis-url] [![JWT][jwt-shield]][jwt-url] [![HTML5][html5-shield]][html5-url] [![CSS3][css3-shield]][css3-url] [![isort][isort-shield]][isort-url] [![Black][black-shield]][black-url] [![Ruff][ruff-shield]][ruff-url] [![MyPy][mypy-shield]][mypy-url] [![pre-commit][pre-commit-shield]][pre-commit-url] [![GitHub Actions][github-actions-shield]][github-actions-url] [![Poetry][poetry-shield]][poetry-url] [![Pycharm][pycharm-shield]][pycharm-url] [![Visual Studio Code][visual-studio-code-shield]][visual-studio-code-url] [![Markdown][markdown-shield]][markdown-url] [![Swagger UI][swagger-ui-shield]][swagger-ui-url] [![License: MIT][license-shield]][license-url]

### Components

Here are the main components of the system:

- **FastAPI Backend**: This is the backend for the mobile app. It's responsible for processing incoming requests, interacting with databases, and returning responses to the client.
- **Databases**: The application uses two types of databases, PostgreSQL for relational data.
- **Redis**: Used for caching and speeding up frequent requests.
- **JWT**: Used for handling authentication.

Each of these components plays a vital role in the functioning of the
backend. Together, they will make up a scalable, maintainable, and robust
application.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->

## Getting started

### Prerequisites

- [Python 3.11][python-docs]

### Installation

1. Clone the **repository**

   ```bash
   git clone https://github.com/jpcadena/fastapi-boilerplate.git
   ```

2. Change the directory to **root project**

   ```bash
   cd fastapi-boilerplate
   ```

3. Install **Poetry** package manager

   ```bash
   pip install poetry
   ```

4. Install the project's **dependencies**

   ```bash
   poetry install
   ```

5. Activate the **environment**

   ```bash
   poetry shell
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->

## Usage

1. **Setting up environment variables:**

   If you find a `.env.sample` in the project directory, make a copy of it and rename to `.env`.

   ```bash
   cp .env.sample .env
   ```

   This `.env` file will be used to manage your application's environment variables.

2. **Configuring your credentials:**

   Open the `.env` file in a text editor and replace the placeholder values with your actual credentials.

   ```bash
   # .env file
   POSTGRES_USER=your_database_user
   SECRET_KEY=your_api_key
   ```

   Be sure to save the file after making these changes.

3. **Generating RSA keys**

    To ensure secure communication in this project, RSA keys are used. Before running the application, you need to generate a public and private RSA key pair.
    We've provided a Python script to automatically generate these keys. You can find the script at `app\services\infrastructure\encryption.py`. To generate your keys, simply run:

    ```bash
    python app\services\infrastructure\encryption.py.py
    ```

    This will create `public_key.pem` and `private_key.pem` files in your specified directory.

    Once the keys are generated, the application will use them for cryptographic operations. Ensure that these files are kept secure and are not exposed publicly. The default configuration expects these keys in the root directory of the project.

4. **Starting the server:**

   To start the local server on your machine, run the following command in your terminal:

   ```bash
   uvicorn main:app --reload
   ```

   The `--reload` flag enables hot reloading, which means the server will automatically update whenever you make changes to the code.

5. **Interacting with the app:**

   Once your server is running, you can interact with it using any API client like Postman or your web browser. You can send GET, POST, PUT, DELETE requests to the API endpoints as defined in your `main.py` file. For example, to get all users, you can send a GET request to `http://localhost:8000/api/v1/users`.

6. **Using Swagger UI:**

   FastAPI provides automatic interactive API documentation using Swagger UI. Once your server is up and running, you can go to `http://localhost:8000/docs` in your web browser to access it. From there, you can explore and interact with your API directly.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- OPENAPI TYPESCRIPT CODEGEN -->

## OpenAPI TypeScript Codegen

To facilitate the interaction between the frontend and the API, we use the [OpenAPI TypeScript Codegen](https://github.com/ferdikoomen/openapi-typescript-codegen) to generate TypeScript models and APIs based on our OpenAPI specification file.

### React Native Installation

First, you need to install the OpenAPI TypeScript Codegen as a devDependency. In your project directory, run:

```bash
npm install openapi-typescript-codegen --save-dev
```

### Codegen Usage

Add the following to your package.json file:

```bash
"generate-client": "openapi --input C:/Users/user/fastapi-boilerplate/openapi.json --output . /src/client --client axios"
```

To generate the TypeScript code, you need to use the openapi.json specification file. Run the following command in your terminal:

```bash
npm run generate-client
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->

## Contributing

[![GitHub][github-shield]][github-url]

Please read our [contributing guide](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- SECURITY -->

## Security

For security considerations and best practices, please refer to our [Security Guide](SECURITY.md) for a detailed guide.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CODE_OF_CONDUCT -->

## Code of Conduct

We enforce a code of conduct for all maintainers and contributors. Please read our [Code of Conduct](CODE_OF_CONDUCT.md) to understand the expectations before making any contributions.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->

## Contact

- [![LinkedIn][linkedin-shield]][linkedin-url]

- [![Outlook][outlook-shield]](mailto:jpcadena@espol.edu.ec?subject=[GitHub]fastapi-boilerplate)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[project-screenshot]: assets/images/project.png
[python-docs]: https://docs.python.org/3.11/

[linkedin-shield]: https://img.shields.io/badge/linkedin-%230077B5.svg?style=for-the-badge&logo=linkedin&logoColor=white
[outlook-shield]: https://img.shields.io/badge/Microsoft_Outlook-0078D4?style=for-the-badge&logo=microsoft-outlook&logoColor=white
[python-shield]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[fastapi-shield]: https://img.shields.io/badge/FastAPI-FFFFFF?style=for-the-badge&logo=fastapi
[pydantic-shield]: https://img.shields.io/badge/Pydantic-FF43A1?style=for-the-badge&logo=pydantic&logoColor=white
[starlette-shield]: https://img.shields.io/badge/Starlette-392939?style=for-the-badge&logo=starlette&logoColor=white
[uvicorn-shield]: https://img.shields.io/badge/Uvicorn-2A308B?style=for-the-badge&logo=uvicorn&logoColor=white
[redis-shield]: https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white
[html5-shield]: https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white
[jwt-shield]: https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens
[pycharm-shield]: https://img.shields.io/badge/PyCharm-21D789?style=for-the-badge&logo=pycharm&logoColor=white
[markdown-shield]: https://img.shields.io/badge/Markdown-000000?style=for-the-badge&logo=markdown&logoColor=white
[swagger-ui-shield]: https://img.shields.io/badge/-Swagger-%23Clojure?style=for-the-badge&logo=swagger&logoColor=white
[github-shield]: https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white
[ruff-shield]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json
[black-shield]: https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge&logo=appveyor
[mypy-shield]: https://img.shields.io/badge/mypy-checked-2A6DB2.svg?style=for-the-badge&logo=appveyor
[visual-studio-code-shield]: https://img.shields.io/badge/Visual_Studio_Code-007ACC?style=for-the-badge&logo=visual-studio-code&logoColor=white
[poetry-shield]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/python-poetry/website/main/static/badge/v0.json
[postgresql-shield]: https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white
[isort-shield]: https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336
[github-actions-shield]: https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white
[pre-commit-shield]: https://img.shields.io/badge/pre--commit-F7B93E?style=for-the-badge&logo=pre-commit&logoColor=white
[css3-shield]: https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white
[license-shield]: https://img.shields.io/badge/License-MIT-yellow.svg

[linkedin-url]: https://linkedin.com/in/juanpablocadenaaguilar
[python-url]: https://docs.python.org/3.11/
[fastapi-url]: https://fastapi.tiangolo.com
[pydantic-url]: https://docs.pydantic.dev
[starlette-url]: https://www.starlette.io/
[uvicorn-url]: https://www.uvicorn.org/
[redis-url]: https://redis.io/
[html5-url]: https://developer.mozilla.org/en-US/docs/Glossary/HTML5
[jwt-url]: https://jwt.io/
[pycharm-url]: https://www.jetbrains.com/pycharm/
[markdown-url]: https://daringfireball.net/projects/markdown/
[swagger-ui-url]: https://swagger.io/
[github-url]: https://github.com/jpcadena/fastapi-boilerplate
[ruff-url]: https://beta.ruff.rs/docs/
[black-url]: https://github.com/psf/black
[mypy-url]: http://mypy-lang.org/
[visual-studio-code-url]: https://code.visualstudio.com/
[poetry-url]: https://python-poetry.org/
[postgresql-url]: https://www.postgresql.org/
[isort-url]: https://pycqa.github.io/isort/
[github-actions-url]: https://github.com/features/actions
[pre-commit-url]: https://pre-commit.com/
[css3-url]: https://developer.mozilla.org/en-US/docs/Web/CSS
[license-url]: https://opensource.org/licenses/MIT
