
using Examples.BadDesign;
namespace Examples.BadDesign.CarExample.CarParts {
public class Wheels {
    int comfort;
    int weight;
    DB db;
    Wheels(int comfort, int weight, int number) {
        this.comfort = comfort;
        this.weight = weight * number;
    }
    int getWeight() {
        return weight;
    }
}
}