# Robotics at Home with Raspberry Pi Pico

<a href="https://www.packtpub.com/product/robotics-at-home-with-raspberry-pi-pico/9781803246079?utm_source=github&utm_medium=repository&utm_campaign=9781803246079"><img src="https://static.packt-cdn.com/products/9781803246079/cover/smaller" alt="" height="256px" align="right"></a>

This is the code repository for [Robotics at Home with Raspberry Pi Pico](https://www.packtpub.com/product/robotics-at-home-with-raspberry-pi-pico/9781803246079?utm_source=github&utm_medium=repository&utm_campaign=9781803246079), published by Packt.

**Build autonomous robots with the versatile low-cost Raspberry Pi Pico controller and Python**

## What is this book about?
The field of robotics is expanding, and this is the perfect time to learn how to create robots at home for different purposes. This book will help you take your first steps in planning, building, and programming a robot with Raspberry Pi Pico, an impressive controller bursting with IO capabilities. After a quick tour of the Pico, you'll begin designing a robot chassis in 3D CAD. With easy-to-follow instructions, shopping lists, and plans, you'll start building the robot. Further, you'll add simple sensors and outputs to extend the robot, reinforce design skills and build knowledge in programming with circuit Python, understand interactions with electronics, standard robotics algorithms, and the discipline and process for building robots. Moving forward, you'll learn to add more complicated sensors and robotic behaviors, with increasing complexity levels, giving you hands-on experience. You'll learn Raspberry Pi Pico's excellent features like PIO, adding capabilities like avoiding walls, detecting movement and compass heading. You'll combine these with Bluetooth BLE for seeing sensor data and remotely control with a smartphone. Finally, you'll program the robot to find its location in an arena.

This book covers the following exciting features:
* Interface Raspberry Pi Pico with motors to move parts
* Design in 3D CAD with Free CAD
* Build a simple robot and extend it for more complex projects
* Interface Raspberry Pi Pico with sensors and Bluetooth BLE
* Visualize robot data with Matplotlib
* Gain an understanding of robotics algorithms on Pico for smart behavior

If you feel this book is for you, get your [copy](https://www.amazon.com/dp/1803246073) today!

<a href="https://www.packtpub.com/?utm_source=github&utm_medium=banner&utm_campaign=GitHubBanner"><img src="https://raw.githubusercontent.com/PacktPublishing/GitHub/master/GitHub.png" 
alt="https://www.packtpub.com/" border="5" /></a>

## Instructions and Navigations
All of the code is organized into folders. For example, ch-01.

A block of code is set as follows:
```
import time
import board
import digitalio

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

while True:
  led.value = True
  time.sleep(0.5)
  led.value = False
  time.sleep(0.5)
```
When we wish to draw your attention to a particular part of a code block, the relevant lines or items are set in bold:
```
>>> 𝗽𝗿𝗶𝗻𝘁("𝗛𝗲𝗹𝗹𝗼, 𝘄𝗼𝗿𝗹𝗱!")
Hello, World!
>>>
```
Any command-line input or output is written as follows:
```
𝗰𝗼𝗱𝗲.𝗽𝘆 𝗼𝘂𝘁𝗽𝘂𝘁:
𝟰𝟰𝟰𝟯 𝟰𝟱𝟮𝟮
```

**Following is what you need for this book:**
This book is for beginner robot makers, keen hobbyists, technical enthusiasts, developers and STEM teachers who want to build robots at home. Prior knowledge of coding - beginner to intermediate programming, will be helpful.

With the following software and hardware list you can run all code files present in the book (Chapter 1-14).
### Software and Hardware List
| Software required | OS required |
| ------------------------------------ | ----------------------------------- |
| Thonny > 3.3 or Mu Editor > 1.1 | macOS, Linux, or Windows |
| Python 3.7 or later | macOS, Linux, or Windows |
| Matplotlib 3.6.1 or later | macOS, Linux, or Windows |
| NumPy 1.23.4 or later | macOS, Linux, or Windows |
| Bleak (Python BLE library) 0.19.0 or above | macOS, Linux, or Windows |
| Free USB port | macOS, Linux, or Windows |
| Smartphone/tablet with Bluetooth LE (Bluetooth > 4.0) | iOS or Android |
| Adafruit Bluefruit LE Connect > 3.3.2 | iOS or Android |
| Bluetooth LE-enabled laptop (or BLE dongle) | macOS, Linux, or Windows |
| FreeCAD | macOS, Linux, or Windows |
| Raspberry Pi Pico |  |
| CircuitPython > 7.2.0 | Raspberry Pi Pico |

We also provide a PDF file that has color images of the screenshots/diagrams used in this book. [Click here to download it](https://packt.link/7x3ku).

### Related products
* Raspberry Pi Pico DIY Workshop [[Packt]](https://www.packtpub.com/product/raspberry-pi-pico-diy-workshop/9781801814812?utm_source=github&utm_medium=repository&utm_campaign=9781801814812) [[Amazon]](https://www.amazon.com/dp/1801814813)

* Learn Robotics Programming - Second Edition [[Packt]](https://www.packtpub.com/product/learn-robotics-programming-second-edition/9781839218804?utm_source=github&utm_medium=repository&utm_campaign=9781839218804) [[Amazon]](https://www.amazon.com/dp/1839218800)

## Get to Know the Author
**Danny Staple**
Danny Staple is an author who builds robots and gadgets at home, and makes videos about his work on the YouTube channel OrionRobots. He attends robotics and maker events such as PiWars and Arduino Day. He's been building robots for 20 years, having run Lego Robotics clubs with Mindstorms and is a mentor at a local CoderDojo, where he teaches kids how to code with Python.
He has been a professional Python programmer since 2009, and a software engineer since 2000. He has worked with embedded systems, throughout the majority of his career. The robots he has built at home with his children include TankBot, SkittleBot (a PiWars 2018 robot), Bangers n Bash (LunchBot), ArmBot, and SpiderBot. He is better at building robots than naming them.

## Other books by the authors
* [Learn Robotics Programming - Second Edition](https://www.packtpub.com/product/learn-robotics-programming-second-edition/9781839218804?utm_source=github&utm_medium=repository&utm_campaign=9781839218804)

### Download a free PDF

 <i>If you have already purchased a print or Kindle version of this book, you can get a DRM-free PDF version at no cost.<br>Simply click on the link to claim your free PDF.</i>
<p align="center"> <a href="https://packt.link/free-ebook/9781803246079">https://packt.link/free-ebook/9781803246079 </a> </p>