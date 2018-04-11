class AssetSale(object):
    def __init__(self, property, aquired_at, sold_at):
        self.property = property
        self.aquired_at = aquired_at
        self.sold_at = sold_at
        self.proceeds = 0
        self.basis = 0

    # gain_loss returns the gain or loss of the AssetSale
    @property
    def gain_loss(self):
        return self.proceeds - self.basis

    # is_loss returns whether the AssetSale is a loss
    def is_loss(self):
        return self.gain_loss < 0
