package Examples.BetterDesign.Repository;

import Examples.BetterDesign.Repository.CarExample.Car;
import Examples.BetterDesign.Repository.CarExample.CarParts.Doors;
import Examples.BetterDesign.Repository.CarExample.CarParts.Driver;
import Examples.BetterDesign.Repository.CarExample.CarParts.Seats;
import Examples.BetterDesign.Repository.CarExample.CarParts.Wheels;


public class DBCar {
    DBCar() {

    }

    String[] getCarsForDriver(Driver driver) {
        return null;
    }

    void updateCar(Car car, Seats seats) {
    }

    void updateCar(Car car, Doors doors) {
    }

    void sellCarTo(Car car, Driver driver) {
    }
    Car getCar(Driver d)
    {
        return new Car();
    }
    Driver getDriver(Car c)
    {
        return new Driver();
    }
    Wheels getWheels(Car c)
    {
        return null;
    }
    Doors getDoors(Car c)
    {
        return null;
    }
    Seats getSeats(Car c)
    {
        return null;
    }
} 