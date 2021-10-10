def robot_control_algorithm(greenPositionCm, bluePositionCm, redPositionCm):

    ##########################################
    # Write the robot control algorithm here #
    ##########################################

    print(
        "[  VISION ] Position of joints: ({}, {}), ({}, {}), ({}, {})".format(
            int(greenPositionCm.x),
            int(greenPositionCm.y),
            int(bluePositionCm.x),
            int(bluePositionCm.y),
            int(redPositionCm.x),
            int(redPositionCm.y),
        )
    )
    # Just for test
    import random
    import time

    random.seed(time.time())
    motorSpeedA = random.uniform(-1, 1)
    motorSpeedB = random.uniform(-1, 1)

    return motorSpeedA, motorSpeedB
