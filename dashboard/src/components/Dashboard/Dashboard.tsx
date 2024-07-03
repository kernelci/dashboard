import SideMenu from "../SideMenu/SideMenu";
import TopBar from "../TopBar/TopBar";
import TreeListingPage from "../TreeListingPage/TreeListingPage";

const Dashboard = () : JSX.Element => {
  return (
    <div className="w-full h-full">
      <div className="flex flex-row w-full justify-between">
        <SideMenu />
        <TopBar />
        <div className="w-full px-16 pt-24 bg-lightGray">
          <TreeListingPage />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
