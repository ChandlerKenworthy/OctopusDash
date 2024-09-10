# Smart Home Dashboard
This project uses Flask along with HTML, CSS and JS (including ChartJS) to make a useable dashboard designed for use in smart homes (i.e. those with an internet connection and smart meter). I leverage the Octopus energy API to get near real-time pricing data for electricity and request the most recent smart meter electricity usage data. This is displayed neatly to the user. I have also trained an LSTM neural network using TensorFlow to predict the price of electricity 1-hr ahead of time. The predictions are shown to the user.

The aim of this is actually so I can more closely monitor my energy usage and use it at better (off-peak) times with the hope that my ML model will be able to give me a 1 hour warning!
