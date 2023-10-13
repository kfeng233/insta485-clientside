import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import InfiniteScroll from "react-infinite-scroll-component";
import Post from "./post";

export default function PostList({ url }) {
  const [posts, setPosts] = useState([]);
  const [next, setNext] = useState("");
  const [hasMore, setHasMore] = useState(true);

  useEffect(() => {
    let ignoreStaleRequest = false;
    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        if (!ignoreStaleRequest) {
          setPosts([...data.results]);
          setNext(data.next);
          setHasMore(Boolean(data.next.length));
          // console.log(data)
        }
      })
      .catch((error) => console.log(error));

    return () => {
      ignoreStaleRequest = true;
    };
  }, [url]);
  const fetchMoreData = () => {
    fetch(next, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        setPosts([...posts, ...data.results]);
        setNext(data.next);
        setHasMore(Boolean(data.next.length));
      })
      .catch((error) => console.log(error));
  };
  return (
    <InfiniteScroll
      dataLength={posts.length}
      next={fetchMoreData}
      hasMore={hasMore}
      loader={<h4>Loading...</h4>}
    >
      <div>
        {posts &&
          posts.map((post) => <Post key={post.postid} url={post.url} />)}
      </div>
    </InfiniteScroll>
  );
}

PostList.propTypes = {
  url: PropTypes.string.isRequired,
};
