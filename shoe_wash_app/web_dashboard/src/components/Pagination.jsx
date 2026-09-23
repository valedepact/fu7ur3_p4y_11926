export default function Pagination({ page, setPage, pageSize, total }) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const start = total === 0 ? 0 : (page - 1) * pageSize + 1;
  const end = Math.min(page * pageSize, total);
  const pageNumbers = Array.from({ length: totalPages }, (_, i) => i + 1).slice(0, 6);

  return (
    <div className="pagination">
      <span>Showing {start}-{end} of {total}</span>
      <div className="pages">
        <button disabled={page === 1} onClick={() => setPage(page - 1)}>&lsaquo;</button>
        {pageNumbers.map((n) => (
          <button key={n} className={n === page ? "active" : ""} onClick={() => setPage(n)}>{n}</button>
        ))}
        <button disabled={page === totalPages} onClick={() => setPage(page + 1)}>&rsaquo;</button>
      </div>
    </div>
  );
}