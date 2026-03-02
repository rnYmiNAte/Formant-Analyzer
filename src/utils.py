def levinson_lpc_autocorr(signal, order):
    """Simple autocorrelation + Levinson-Durbin LPC solver."""
    if len(signal) < order + 1:
        return np.zeros(order + 1)
    
    # Autocorrelation
    r = np.correlate(signal, signal, mode='full')[len(signal)-1:]
    r = r[:order+1] / len(signal)  # normalize
    
    a = np.zeros(order + 1)
    a[0] = 1.0
    e = r[0]
    
    for k in range(1, order + 1):
        lambda_ = -np.dot(r[1:k+1], a[1:k][::-1]) / e
        a_new = np.copy(a)
        for j in range(1, k):
            a_new[j] = a[j] + lambda_ * a[k-j]
        a_new[k] = lambda_
        e = e * (1 - lambda_**2)
        a = a_new
    
    return a
