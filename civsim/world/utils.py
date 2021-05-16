def messy_noise(val, noise_set):
    return noise_set[0](val)+0.5*noise_set[1](val)+0.25*noise_set[2](val)
