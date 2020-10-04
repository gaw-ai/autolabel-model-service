# autolabel-template-matching-service
Autolabel template matching service

## How to (Docker)

1. Run `build.sh` to set-up base Docker image for running the service.

```bash
./build.sh
```

2. Copy `config.env.default` to `config.env`. Then, set-up `G_RAY_ADDRESS` to the machine address (local/public), e.g., `172.17.0.1`.

3. Start Ray cluster as the head node machine by running `start_head_node.sh`.

```bash
./start_head_node.sh
```
4. Run `exec_head_serve.sh` to start serving the service.

```bash
./exec_head_serve.sh
```

5. Try access the machine address at port 3080. There should be a welcome message.
6. To stop the service, do it using `docker stop`. Do `docker rm` the stopped container if necessary.

## How to (virtualenv)

1. Install all Python requirements.

```bash
pip3 install -r requirements.txt
```

2. Copy `config.env.default` to `config.env`. Then, set-up `G_RAY_ADDRESS` to the machine address (local/public), e.g., `127.0.0.1`.

3. Start Ray cluster as the head node machine by running `ray_node_scripts/ray_start_head.sh`.

```bash
cd ray_node_scripts
./ray_start_head.sh
```
4. Run `exec_head_serve.sh` to start serving the service.

```bash
cd autolabel_models
python3 start_serving.py
```

5. Try access the machine address at port 3080. There should be a welcome message.
6. To stop the service, do it using `ray stop`.
