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
        // A response arrives after a newer request has been made,
        // which means that a newer request has been made before the
        // previous request has completed.
        if (!ignoreStaleRequest) {
          setPosts([...data.results]);
          setNext(data.next);
          setHasMore(Boolean(data.next.length));
        }
      })
      .catch((error) => console.log(error));

    return () => {
      ignoreStaleRequest = true;
    };
  }, [url]);

  // fetch more data and update the component's state with new posts.
  // used as the 'next' callback for the InfiniteScroll component.
  const fetchMoreData = async () => {
    try {
      // await to not execute the subsequent code until the current asyn
      // operation is complete
      const response = await fetch(next, { credentials: "same-origin" });
      if (!response.ok) throw Error(response.statusText);
      const data = await response.json();
      // state won't update if an error is thrown during the fetch operation
      setPosts([...posts, ...data.results]);
      setNext(data.next);
      setHasMore(Boolean(data.next.length));
    } catch (error) {
      console.log(error);
    }
  };

  return (
    <div>
      <InfiniteScroll
        dataLength={posts.length} // This is important field to render the next data
        next={fetchMoreData}
        hasMore={hasMore}
        loader={<h4 style={{ textAlign: "center" }}>Loading...</h4>}
        endMessage={
          <p style={{ textAlign: "center" }}>
            <b>Yay! You have seen it all</b>
          </p>
        }
      >
        {posts &&
          posts.map((post) => <Post key={post.postid} url={post.url} />)}
      </InfiniteScroll>
    </div>
  );
}

PostList.propTypes = {
  url: PropTypes.string.isRequired,
};
