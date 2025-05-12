import { useEffect, useState } from 'react';
import axios from 'axios';
import { API_BASE_URL } from './api';

function SnapshotViewer() {
  const [snapshots, setSnapshots] = useState([]);

  useEffect(() => {
    const fetchSnapshots = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/list_snapshots`);
        setSnapshots(response.data.snapshots);
      } catch (error) {
        console.error('Error fetching snapshots:', error);
      }
    };

    fetchSnapshots();
  }, []);
  
  const handleView = (snapshot) => {
	  const viewUrl = `${API_BASE_URL}/snapshots/${snapshot}`;
	  window.open(
		viewUrl,
		'_blank',
		'width=800,height=600,resizable=yes,scrollbars=yes'
	  );
  };

  const handleDownload = (snapshot) => {
    const downloadUrl = `${API_BASE_URL}/snapshots/${snapshot}`;
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.setAttribute('download', snapshot);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleDelete = async (snapshot) => {
    try {
      await axios.delete(`${API_BASE_URL}/delete_snapshot/${snapshot}`);
      setSnapshots((prev) => prev.filter((s) => s !== snapshot));
    } catch (error) {
      console.error('Error deleting snapshot:', error);
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-md mt-8">
      <h2 className="text-2xl font-bold mb-4 text-center">📦 Available Snapshots</h2>
      <ul className="space-y-2">
        {snapshots.map((snapshot) => (
          <li key={snapshot} className="flex justify-between items-center">
            <span>{snapshot}</span>
            <div className="space-x-4">
			  <button
				  onClick={() => handleView(snapshot)}
				  className="text-green-600 hover:underline"
				>
				  View
			  </button>
              <button
                onClick={() => handleDownload(snapshot)}
                className="text-blue-600 hover:underline"
              >
                Download
              </button>
              <button
                onClick={() => handleDelete(snapshot)}
                className="text-red-600 hover:underline"
              >
                Delete
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default SnapshotViewer;
