package Examples.BetterDesign.Repository;
import Examples.BetterDesign.Repository.WarehouseEntities.Car;
import Examples.BetterDesign.Repository.WarehouseEntities.Complaints;
import Examples.BetterDesign.Repository.WarehouseEntities.Customer;
import Examples.BetterDesign.Repository.WarehouseEntities.Invoice;
import Examples.BetterDesign.Repository.WarehouseEntities.User;

public class DBWarehouse {
    Customer getCustomer(Invoice i) {
        return null;
    }
    Car getCar(Complaints c) {
        return null;
    }
    Invoice getInvoice(Customer c) {
        return null;
    }
    Complaints getComplaints(Customer c) {
        return null;
    }
    User getUser(Car car) {
        return null;
    }
    Customer getCustomer(Complaints complaint) {
        return null;
    }
    Car getCar(User user) {
        return null;
    }
    Complaints getComplaints(Car car) {
        return null;
    }
    User getFirstUser() {
        return null;
    }
    Car getFirstCar() {
        return null;
    }
    Invoice getFirstInvoice() {
        return null;
    }
    Complaints getFirstComplaints() {
        return null;
    }
}
