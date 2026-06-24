# Handheld Celestial Tracker 🌌

I am currently building a portable, hardware-based handheld celestial tracking system. The goal of this project is to calculate and track planetary positions, right ascension (RA), declination (Dec), and coordinate transformations in real-time, right from a handheld device. This project serves as a practical tool for sky-gazing, coordinates calculations, and portfolio development for the Astronomy Olympiad.

---

## 🔍 Detailed Device Workflow

The device operates as a real-time tracking bridge between your physical orientation on Earth and the celestial sphere. Here is exactly how the system functions when you hold it up to the night sky:

1. **Location & Time Synchronization:** When powered on, the onboard GPS module establishes a satellite lock to acquire your precise Geodetic coordinates (Latitude and Longitude) along with the current Universal Time Coordinated (UTC).
2. **Time Conversion:** The Python backend takes the UTC time and calculates the **Julian Date**, which is then converted into **Local Sidereal Time (LST)** based on your current longitude. This is crucial for tracking how the sky shifts relative to your position over time.
3. **Orientation Sensing:** As you aim the handheld device at a target in the sky, the integrated digital compass (magnetometer) tracks the device's precise heading/azimuth relative to Magnetic North (corrected to True North), while an IMU/tilt sensor calculates the altitude angle relative to your local horizon.
4. **Celestial Math Engine:** Using `NumPy` and `SymPy`, the system computes the target planet's true orbital position using its Keplerian orbital elements relative to the **Vernal Equinox** reference framework. 
5. **Coordinate Transformation:** The script runs matrix transformations to convert the object's Equatorial coordinates (Right Ascension and Declination) into Horizontal coordinates (Altitude and Azimuth) specific to your location.
6. **Live Feedback:** The OLED display screen dynamically guides your aim, updating in real-time to show how many degrees left, right, up, or down you need to move the device to center on the target planet or star.

---

## 🛠️ Hardware Stack & Components Explained

Here are the specific physical components I am using to build this device:

* **Raspberry Pi 3 Model B+**
  * *Role:* The central brain of the device. It runs the lightweight Linux environment, executes the core Python algorithms, handles data streams from the sensors via GPIO/I2C/Serial pins, and outputs data to the display.
* **GPS Module**
  * *Role:* Provides the exact geographic positioning and atomic-clock accurate time required to ground the celestial coordinate transformations to your specific spot on Earth.
* **Digital Compass / Magnetometer**
  * *Role:* Tracks the physical orientation and spatial tilt of the handheld device, providing the live azimuth (directional heading) data needed to match where the device is pointing with the celestial map.
* **OLED Display Screen**
  * *Role:* A high-contrast, low-power compact screen that outputs real-time navigation guidance, current Julian dates, and target RA/Dec coordinates without ruining your night-vision adjustments.

---

## 💻 Tech Stack & Software Libraries

* **Language:** Python
* **Data Manipulation (`NumPy`):** Handles high-speed matrix math, array manipulations, and trigonometry operations required for converting coordinate frameworks instantly.
* **Symbolic Math (`SymPy`):** Used for managing analytical geometric equations and verifying the symbolic orbital paths of tracking targets.
* **Hardware Interfacing (`LeadControl` & GPIO):** Manages data capture timings from the sensors and controls peripheral signals or motor adjustments if automated tracking is toggled.

---


