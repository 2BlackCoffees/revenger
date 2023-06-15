
using Examples.BetterDesign.Repository;
namespace Examples.BetterDesign.Repository.CarExample.CarParts {

public class Doors {
    DBCar db;
    int comfort;
    int weight;
    Doors(int comfort, int weight, int number) {
        this.comfort = comfort;
        this.weight = weight * number;
    }
    int getWeight() {
        return weight;
    }
}
}