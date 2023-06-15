
using Examples.BetterDesign.Repository;
namespace Examples.BetterDesign.Repository.CarExample.CarParts {

public class Driver {
    int weight;
    DBCar db;
    public Driver() {

    }
    Driver(int weight) {
        this.weight = weight;
    }
    int getWeight() {
        return weight;
    }
}
}