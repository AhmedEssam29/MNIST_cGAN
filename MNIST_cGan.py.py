# -*- coding: utf-8 -*-
"""Untitled15.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1bbC7x1NkpM-0plSN1cQa4sJHVrMFKATu
"""

from google.colab import drive
drive.mount('/content/drive')

import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, Reshape, Flatten, Dropout, BatchNormalization, LeakyReLU, UpSampling2D, Conv2D
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.optimizers.legacy import Adam  # Use the legacy Adam optimizer
import numpy as np
import matplotlib.pyplot as plt
import os

def build_generator(latent_dim, num_classes, img_shape):
    model = Sequential()

    model.add(Dense(128 * 7 * 7, activation="relu", input_dim=latent_dim + num_classes))
    model.add(Reshape((7, 7, 128)))
    model.add(UpSampling2D())
    model.add(Conv2D(128, kernel_size=3, padding="same"))
    model.add(BatchNormalization(momentum=0.8))
    model.add(LeakyReLU(alpha=0.2))
    model.add(UpSampling2D())
    model.add(Conv2D(64, kernel_size=3, padding="same"))
    model.add(BatchNormalization(momentum=0.8))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Conv2D(img_shape[2], kernel_size=3, padding="same"))
    model.add(tf.keras.layers.Activation("tanh"))

    noise = Input(shape=(latent_dim,))
    label = Input(shape=(num_classes,))
    model_input = tf.keras.layers.Concatenate()([noise, label])

    img = model(model_input)

    return Model([noise, label], img)

def build_discriminator(img_shape, num_classes):
    img = Input(shape=img_shape)
    label = Input(shape=(num_classes,))

    # Expand the label dimensions to match the image dimensions
    label_embedding = Dense(img_shape[0] * img_shape[1], activation='linear')(label)
    label_embedding = Reshape((img_shape[0], img_shape[1], 1))(label_embedding)

    # Concatenate the image and the label embedding
    concatenated = tf.keras.layers.Concatenate(axis=-1)([img, label_embedding])

    model = Sequential()

    model.add(Conv2D(64, kernel_size=3, strides=2, input_shape=(img_shape[0], img_shape[1], img_shape[2] + 1), padding="same"))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Dropout(0.25))
    model.add(Conv2D(128, kernel_size=3, strides=2, padding="same"))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Dropout(0.25))
    model.add(Flatten())
    model.add(Dense(1, activation='sigmoid'))

    validity = model(concatenated)

    return Model([img, label], validity)

def compile_gan(generator, discriminator, latent_dim, num_classes, img_shape):
    optimizer = Adam(0.0002, 0.5)

    discriminator.compile(loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])

    noise = Input(shape=(latent_dim,))
    label = Input(shape=(num_classes,))
    img = generator([noise, label])

    discriminator.trainable = False
    validity = discriminator([img, label])

    combined = Model([noise, label], validity)
    combined.compile(loss='binary_crossentropy', optimizer=optimizer)

    return combined

def train(generator, discriminator, combined, epochs, batch_size, latent_dim, num_classes, img_shape, X_train, y_train):
    half_batch = batch_size // 2

    for epoch in range(epochs):
        # Train Discriminator
        idx = np.random.randint(0, X_train.shape[0], half_batch)
        imgs = X_train[idx]
        labels = y_train[idx]

        noise = np.random.normal(0, 1, (half_batch, latent_dim))
        gen_labels = np.random.randint(0, num_classes, half_batch)
        gen_labels_onehot = tf.keras.utils.to_categorical(gen_labels, num_classes=num_classes)
        gen_imgs = generator.predict([noise, gen_labels_onehot])

        valid = np.ones((half_batch, 1))
        fake = np.zeros((half_batch, 1))

        d_loss_real = discriminator.train_on_batch([imgs, labels], valid)
        d_loss_fake = discriminator.train_on_batch([gen_imgs, gen_labels_onehot], fake)
        d_loss = 0.5 * np.add(d_loss_real, d_loss_fake)

        # Train Generator
        noise = np.random.normal(0, 1, (batch_size, latent_dim))
        labels = np.random.randint(0, num_classes, batch_size)
        labels_onehot = tf.keras.utils.to_categorical(labels, num_classes=num_classes)
        valid = np.ones((batch_size, 1))

        g_loss = combined.train_on_batch([noise, labels_onehot], valid)

        print(f"{epoch} [D loss: {d_loss[0]}, acc.: {100 * d_loss[1]}] [G loss: {g_loss}]")

        # Save generated samples periodically
        if epoch % 100 == 0:
            save_imgs(generator, epoch, latent_dim, num_classes, img_shape, "/content/drive/MyDrive/cGAN")



def save_imgs(generator, epoch, latent_dim, num_classes, img_shape, save_path):
    r, c = 5, 5
    noise = np.random.normal(0, 1, (r * c, latent_dim))
    labels = np.array([num for _ in range(r) for num in range(c)])
    labels_onehot = tf.keras.utils.to_categorical(labels, num_classes=num_classes)

    gen_imgs = generator.predict([noise, labels_onehot])
    gen_imgs = 0.5 * gen_imgs + 0.5  # Rescale to [0, 1]

    fig, axs = plt.subplots(r, c)
    cnt = 0
    for i in range(r):
        for j in range(c):
            axs[i, j].imshow(gen_imgs[cnt, :, :, 0], cmap='gray')
            axs[i, j].axis('off')
            cnt += 1

    # Create the directory if it doesn't exist
    os.makedirs(save_path, exist_ok=True)

    # Save the generated images
    fig.savefig(os.path.join(save_path, f"generated_images_{epoch}.png"))
    plt.close()


# Hyperparameters
latent_dim = 100  # The size of the latent vector
num_classes = 10  # Number of different architectural styles or building types
img_shape = (28, 28, 1)  # Assuming grayscale images for simplicity

# Build and compile models
generator = build_generator(latent_dim, num_classes, img_shape)
discriminator = build_discriminator(img_shape, num_classes)
combined = compile_gan(generator, discriminator, latent_dim, num_classes, img_shape)

# Load and preprocess your dataset
(X_train, y_train), (_, _) = tf.keras.datasets.mnist.load_data()  # Replace with your dataset
X_train = X_train / 127.5 - 1.0  # Normalize to [-1, 1]
X_train = np.expand_dims(X_train, axis=-1)
y_train = tf.keras.utils.to_categorical(y_train, num_classes=num_classes)

# Train the GAN
train(generator, discriminator, combined, epochs=10000, batch_size=64, latent_dim=latent_dim, num_classes=num_classes, img_shape=img_shape, X_train=X_train, y_train=y_train)

