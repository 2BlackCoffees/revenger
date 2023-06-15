package Examples.BetterDesign.Repository.CarExample;

import Examples.BetterDesign.Repository.CarExample.CarParts.Doors;
import Examples.BetterDesign.Repository.CarExample.CarParts.Driver;
import Examples.BetterDesign.Repository.CarExample.CarParts.Seats;
import Examples.BetterDesign.Repository.CarExample.CarParts.Wheels;
import Examples.BetterDesign.Repository.DBCar;

class Vehicle
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
public class Car extends Vehicle {
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
