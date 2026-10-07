# Principles of Robot Autonomy I HW1
Homework 1 code for Principles of Robot Autonomy I
## Dependencies
Python package dependencies for this assignment are listed in the `requirements.txt` file and can be automatically installed by
```
pip install -r requirements.txt
```

## Problem 3.8.b
Need
```
|1 - 0.1*kp| < 1
-1 < 1 - 0.1*kp < 1
-2 < -0.1*kp < 0
0 < 0.1*kp < 2
```
So
```
0 < kp < 20
```
Where `kp < 10` would make it exponentially decay, but `kp > 10` would cause the coefficient of `e_k` to be negative, which would cause sinusoidal motion, but it would still be bound by an exponential decay envelope.

Then, if `kp < 0`, error would just grow, and if `kp > 20` the error would stil be sinusoidal, but it would grow exponentially as well.

## Problem 3.8.c

```
|w| < w_max
-w_max < w < w_max
-w_max < kp*e < w_max
-w_max < kp*(goal - theta) < w_max
-w_max/kp < goal - theta < w_max/kp
-w_max/kp < goal - theta < w_max/kp
-w_max/kp - goal < -theta < w_max/kp - goal
-w_max/kp + goal < theta < w_max/kp + goal
```
And plugging in `w_max = 0.4`, `goal = 1.274`, and `kp = 2` we get:
```
1.074 < theta < 1.474
```
So if `theta` is not within these bounds, the commanded `omega` will be larger than the threshold. Therefore, when the angle is smaller than the lower bound, the commanded angular velocity will saturate, so it will not travel as fast as it would if it were being commanded to the actual omega from the representative error. 

For reasons why `kp` cannot be arbitrarily large:

1. As stated in part b., it might cause the robot to under- or overshoot 
2. It might reach the physical limits of the motor itself. If this happens, it may try to command the motor to a higher `omega` than it is allowed to go, but the motor would saturate, and there would still be an error no matter how long the robot commands that `omega`. This could cause windup if there is an integral controller.