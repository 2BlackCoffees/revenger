
using Examples.BetterDesign.Repository.CarExample.CarParts;
using Examples.BetterDesign.Repository;

namespace Examples.BetterDesign.Repository.CarExample {
public class Vehicle
{
    int speed;
    DBCar db;
    public Vehicle()
    {

    }
    void setSpeed(int speed) {
        this.speed = speed;
    }
    int getSpeed() {
        return speed;
    }
}
public class Car : Vehicle {
    Wheels wheels;
    Seats seats;
    Driver driver;
    Doors doors;

    public Car()
    {}
    void createCar(Doors doors)
    {
    }
}
}