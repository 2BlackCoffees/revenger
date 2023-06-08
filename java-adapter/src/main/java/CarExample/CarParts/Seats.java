package CarExample.CarParts;

public class Seats {
    int comfort;
    int weight;
    Seats(int comfort, int weight, int number) {
        this.comfort = comfort;
        this.weight = weight * number;
    }
    int getWeight() {
        return weight;
    }
}
