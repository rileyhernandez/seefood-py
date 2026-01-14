# Seefood-py

This project contains the Python source code for the Seefood embedded device, which is a restaurant data collection device designed to weigh and take pictures of outgoing meals. The collected data is used for analytics, including employing computer vision to detect incorrect items and provide evidence for fraudulent refund requests. Eventually, the device will provide real-time error detection on-device.

The current hardware setup includes a Raspberry Pi Zero 2W or a Raspberry Pi 4B, a USB webcam, and a NAU7802 load cell amplifier for weighing.

## Installation

This project uses `uv` for dependency management. To install the required packages, run:

```bash
uv sync
```

## Configuration

### Environment Variables

Create a `.env` file in the root of the project. You can use the `.env.example` file as a template:

```bash
cp .env.example .env
```

Then, edit the `.env` file with the following values:

-   `GCP_KEY`: Your Google Cloud Platform API key.
-   `BACKEND_URL`: The URL of the production backend server.
-   `DEV_BACKEND_URL`: The URL of the development backend server.
-   `CONFIG_PATH`: The path to the `config.toml` file.

### TOML Configuration

Create a `config.toml` file. You can use the `config.toml.example` file as a template:

```bash
cp config.toml.example config.toml
```

The `config.toml` file contains hardware-specific configurations for the device, such as camera settings, scale settings, and GPIO pin numbers.

### Enable I2C (Raspberry Pi)

The NAU7802 load cell amplifier communicates via I2C. To enable the I2C interface on your Raspberry Pi:

1.  Open the terminal and run:
    ```bash
    sudo raspi-config
    ```
2.  Navigate to `3 Interface Options`.
3.  Select `I5 I2C`.
4.  Choose `<Yes>` when asked if you would like the ARM I2C interface to be enabled.
5.  Select `<Ok>` and then `<Finish>` to exit `raspi-config`. You may need to reboot your Raspberry Pi for the changes to take effect.

## Running the Application

To run the main application, execute the `src/main.py` script:

```bash
python src/main.py
```

You can also run the application in development mode by passing the `dev` argument:

```bash
python src/main.py dev
```

## Testing

### Test Server

The `src/testing/test_server.py` script runs a local Flask server that simulates the backend. This is useful for testing the device without a live backend. To run the test server:

```bash
python src/testing/test_server.py
```

The server will be available at `http://localhost:8080`.

### Test Client

The `src/testing/test_client.py` script simulates the Seefood device and sends data to the test server. To run the test client:

```bash
python src/testing/test_client.py
```

The test client can also be used to test individual hardware components:

-   **LEDs:** `python src/testing/test_client.py led`
-   **Button:** `python src/testing/test_client.py button`
-   **LEDs and Button:** `python src/testing/test_client.py led-button`