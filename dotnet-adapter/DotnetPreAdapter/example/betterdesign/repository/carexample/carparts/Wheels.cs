
using Examples.BetterDesign.Repository;
namespace Examples.BetterDesign.Repository.CarExample.CarParts {

public class Wheels {
    int comfort;
    int weight;
    DBCar db;
    Wheels(int comfort, int weight, int number) {
        this.comfort = comfort;
        this.weight = weight * number;
    }
    int getWeight() {
        return weight;
    }
}
}