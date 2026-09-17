from dataclasses import dataclass
@dataclass
class ModelRunner:
    model: object
    def run(self, spark):
        return self.model.run(spark)
