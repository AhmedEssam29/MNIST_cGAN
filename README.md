# MNIST_cGAN
# GAN for Generating Numbers using MNIST

This project leverages Generative Adversarial Networks (GANs) to generate precise Numbers.
## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Model Description](#model-description)
- [Training the Model](#training-the-model)
- [Generating Images](#generating-images)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/gan-architectural-drawings.git
    cd gan-architectural-drawings
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Ensure you have your dataset prepared. This example uses the MNIST dataset for demonstration. Replace it with your architectural drawing dataset.

2. Run the training script:
    ```bash
    python train_gan.py
    ```

3. Generated images will be saved periodically during training in the current directory.

## Project Structure


## Model Description

The GAN consists of two main components:

- **Generator:** Generates new architectural drawings from random noise and conditional labels.
- **Discriminator:** Evaluates the generated drawings for authenticity and correctness based on the given labels.

### Generator Architecture

- Fully connected and reshaping layers.
- Up-sampling and convolutional layers with batch normalization and LeakyReLU activations.
- Outputs a generated image using a `tanh` activation function.

### Discriminator Architecture

- Convolutional layers with LeakyReLU activations and dropout for regularization.
- The input image is concatenated with a label embedding.
- Outputs a single value representing the validity of the image.

## Training the Model

The training process involves alternating between training the discriminator and the generator:

1. **Train Discriminator:**
    - On real images with correct labels.
    - On fake images generated by the generator with random labels.

2. **Train Generator:**
    - Attempt to fool the discriminator into thinking the generated images are real.

Training continues for a specified number of epochs, with intermediate results saved periodically.

## Generating Images

After training, you can use the trained generator model to create new architectural drawings:

```python
import numpy as np
from gan import build_generator

# Load the trained generator model
generator = build_generator(latent_dim=100, num_classes=10, img_shape=(28, 28, 1))
generator.load_weights('path_to_generator_weights.h5')

# Generate new images
noise = np.random.normal(0, 1, (10, 100))
labels = np.random.randint(0, 10, 10)
labels_onehot = tf.keras.utils.to_categorical(labels, num_classes=10)
gen_imgs = generator.predict([noise, labels_onehot])

# Save or display generated images
