
using Examples.BadDesign;
namespace Examples.BadDesign.CarExample.CarParts {

public class Seats {
    int comfort;
    int weight;
    DB db;
    Seats(int comfort, int weight, int number) {
        this.comfort = comfort;
        this.weight = weight * number;
    }
    int getWeight() {
        return weight;
    }
}
}